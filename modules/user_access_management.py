import os
import subprocess

def create_user(username, password=None, home_dir=None, shell=None):
    """
    Creates a new user on the system.

    :param username: Name of the user to create
    :param password: Password for the new user (optional)
    :param home_dir: Home directory for the user (optional)
    :param shell: Default shell for the user (optional)
    :return: True if the user was created successfully, False otherwise
    """
    command = ['sudo', 'useradd']
    
    if home_dir:
        command.extend(['-d', home_dir])
    if shell:
        command.extend(['-s', shell])
    
    command.append(username)
    
    try:
        subprocess.run(command, check=True)
        
        if password:
            subprocess.run(['sudo', 'chpasswd'], input=f'{username}:{password}', text=True, check=True)
        
        print(f"User {username} created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating user {username}: {e}")
        return False

def delete_user(username, remove_home=False):
    """
    Deletes a user from the system.

    :param username: Name of the user to delete
    :param remove_home: If True, remove the user's home directory as well
    :return: True if the user was deleted successfully, False otherwise
    """
    command = ['sudo', 'userdel']
    
    if remove_home:
        command.append('-r')
    
    command.append(username)
    
    try:
        subprocess.run(command, check=True)
        print(f"User {username} deleted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error deleting user {username}: {e}")
        return False

def add_user_to_group(username, group):
    """
    Adds a user to a group.

    :param username: Name of the user to add to the group
    :param group: Name of the group
    :return: True if the user was added successfully, False otherwise
    """
    try:
        subprocess.run(['sudo', 'usermod', '-aG', group, username], check=True)
        print(f"User {username} added to group {group} successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding user {username} to group {group}: {e}")
        return False

def remove_user_from_group(username, group):
    """
    Removes a user from a group.

    :param username: Name of the user to remove from the group
    :param group: Name of the group
    :return: True if the user was removed successfully, False otherwise
    """
    try:
        # Fetch the user's current groups
        current_groups = subprocess.check_output(['groups', username], text=True).strip().split(': ')[1].split()
        
        # Remove the target group from the user's groups
        new_groups = ','.join(g for g in current_groups if g != group)
        
        subprocess.run(['sudo', 'usermod', '-G', new_groups, username], check=True)
        print(f"User {username} removed from group {group} successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error removing user {username} from group {group}: {e}")
        return False

def change_user_password(username, new_password):
    """
    Changes the password for a user.

    :param username: Name of the user whose password to change
    :param new_password: The new password for the user
    :return: True if the password was changed successfully, False otherwise
    """
    try:
        subprocess.run(['sudo', 'chpasswd'], input=f'{username}:{new_password}', text=True, check=True)
        print(f"Password for user {username} changed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error changing password for user {username}: {e}")
        return False

def lock_user_account(username):
    """
    Locks a user account.

    :param username: Name of the user to lock
    :return: True if the account was locked successfully, False otherwise
    """
    try:
        subprocess.run(['sudo', 'usermod', '-L', username], check=True)
        print(f"User {username} account locked successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error locking user account for {username}: {e}")
        return False

def unlock_user_account(username):
    """
    Unlocks a user account.

    :param username: Name of the user to unlock
    :return: True if the account was unlocked successfully, False otherwise
    """
    try:
        subprocess.run(['sudo', 'usermod', '-U', username], check=True)
        print(f"User {username} account unlocked successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error unlocking user account for {username}: {e}")
        return False

def list_all_users():
    """
    Lists all users on the system.

    :return: A list of usernames
    """
    try:
        users = subprocess.check_output(['cut', '-d:', '-f1', '/etc/passwd'], text=True).splitlines()
        print("List of all users on the system:")
        for user in users:
            print(f"  - {user}")
        return users
    except subprocess.CalledProcessError as e:
        print(f"Error listing users: {e}")
        return []

def list_user_groups(username):
    """
    Lists all groups a user is part of.

    :param username: Name of the user
    :return: A list of groups
    """
    try:
        groups = subprocess.check_output(['groups', username], text=True).strip().split(': ')[1].split()
        print(f"User {username} is part of the following groups: {', '.join(groups)}")
        return groups
    except subprocess.CalledProcessError as e:
        print(f"Error listing groups for user {username}: {e}")
        return []

if __name__ == "__main__":
    # Example usage:
    create_user('newuser', password='newpassword', home_dir='/home/newuser', shell='/bin/bash')
    add_user_to_group('newuser', 'sudo')
    list_user_groups('newuser')
    change_user_password('newuser', 'evennewerpassword')
    lock_user_account('newuser')
    unlock_user_account('newuser')
    remove_user_from_group('newuser', 'sudo')
    delete_user('newuser', remove_home=True)
