import subprocess
import functools
import argparse
import ctypes
import sys
import os

REGISTRY_PATH = 'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options'

def set_priviledged_task(name, file_path):
    exists = subprocess.run(['schtasks', '/Query', '/FO', 'CSV', '/NH', '/TN', name],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if exists.returncode == 1:  # Task does not exist
        subprocess.run(['schtasks', '/Create', '/SC', 'ONCE', '/TN', name,
                        '/TR', file_path, '/ST', '00:01', '/IT', '/F', '/RL', 'HIGHEST'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return f'schtasks /Run /TN "{name}"'

def add_interception(executable_path, target):
    executable = os.path.basename(executable_path)
    executable_reg_path = os.path.join(REGISTRY_PATH, executable)

    task_name = f'Procrastinot ({executable})'
    deny_cmd = target + ' "' + executable_path + '"'

    task_run_cmd = set_priviledged_task(task_name, deny_cmd)
    run_cmd = rf'C:\Windows\System32\cmd.exe /K {task_run_cmd} && taskkill /IM cmd.exe & cd'

    subprocess.run(['reg', 'add', executable_reg_path, '/v', 'Debugger',
                    '/d', run_cmd, '/f'])

def clear_interception(executable):
    executable_reg_path = os.path.join(REGISTRY_PATH, executable)
    subprocess.run(['schtasks', '/Delete', '/TN', f'Procrastinot ({executable})', '/F'],
                   stdout=subprocess.PIPE)
    subprocess.run(['reg', 'delete', executable_reg_path, '/f'], stderr=subprocess.PIPE)

def check_for_interception(executable):
    ps = subprocess.Popen(['reg', 'query', os.path.join(REGISTRY_PATH, executable), '/v', 'Debugger'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = ps.communicate()
    return not error

def list_interceptions(target):
    ps = subprocess.Popen(['reg', 'query', REGISTRY_PATH], stdout=subprocess.PIPE)
    output = ps.communicate()[0]
    files = [os.path.basename(path.strip()) for path in output.decode().strip().split('\n')]

    return filter(check_for_interception, files)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', '-a', dest='add', metavar='EXECUTABLE', help='Add an interception')
    parser.add_argument('--remove', '-r', dest='remove', metavar='EXECUTABLE', help='Remove an interception')
    parser.add_argument('--target', '-t', dest='target', help='Specify where to point the intercepted executable to')
    parser.add_argument('--list', '-l', default=False, action='store_true' , help='List all interceptions pointed to a target')

    args = parser.parse_args()

    if args.add or args.remove:
        if args.add and args.target:
            add_interception(args.add, target=args.target)
        elif args.remove:
            clear_interception(args.remove)
    elif args.list:
        for interception in list_interceptions(args.list):
            print(interception)
