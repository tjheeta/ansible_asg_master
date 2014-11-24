Role Name
=========

This sets up an ansible master server which can respond to callbacks from an autoscale group on EC2 . For this to happen, it copies your roles, playbooks, and inventory setup from local to the remote host. Additionally, it needs to have some AWS variables setup. 

Requirements
------------

This will only run on Ubuntu / Debian

Role Variables
--------------

These are the variables that should be overwritten in your playbook:

ansible_asg_local_roles_path: ~/ansible/roles
ansible_asg_local_inventory_path: ~/ansible/inventory
ansible_asg_local_playbook_path: ~/ansible/playbooks
aws_ssh_private_key: ~/ansible/aws_key.pem
aws_remote_user: ubuntu
aws_access_key_id: YOUR_ACCESS_KEY
aws_secret_access_key: YOUR_SECRET_KEY
aws_region: us-east-1
app:
  hashes:
    596524d707e18a17ee521f7710d628e3: worker.yml
  port: 9001


Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
