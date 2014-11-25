Ansible Autoscale Master
=========

This sets up an ansible master server which can respond to callbacks from an autoscale group on EC2 . For this to happen, it copies your roles, playbooks, and inventory setup from local to the remote host. Additionally, it needs to have some AWS variables setup. 

It does the following during the bootstrap:

* ansible.yml - sets up ansible with .boto.cfg, .ansible.cfg, and the private key specified
* sync.yml - copies over roles, inventory, and playbooks from your local machine specified in the variables ansible_asg_local\*..
* app.yml - sets up the callback application. There are some variables that need to be set such as port and hashes.

The callback application:

* responds over HTTP to /api/ec2/asg/$id.
* If the variable *ansible_asg_app['hashes']* has been setup, it uses that to translate $id -> playbook. This is a bit of security through obsucurity, but may help if you want to setup a public facing server and don't want to expose all the playbooks. If it's not setup, it will look just use the $id as the playbook, which is the default.
```
ansible_asg_app:
  hashes:
      596524d707e18a17ee521f7710d628e3: worker.yml
```
* checks that the calling ip exists in the instances in the region on your EC2 account.
* runs the ansible playbook specified on the calling ip.

Requirements
------------

This has been only tested on Ubuntu 14.04 for packages python-boto. 
This assumes that it will be running on EC2 and needs .boto to be setup
```
cat ~/.boto 
[Credentials]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Role Variables
--------------

These are the variables that should be overwritten in your playbook in playbooks/group_vars/all:
```
ansible_asg_local_roles_path: /home/self/ansible/roles
ansible_asg_local_inventory_path: /home/self/ansible/inventory
ansible_asg_local_playbook_path: /home/self/ansible/playbooks
aws_ssh_private_key: /home/self/ec2_private_key.pem
aws_remote_user: ubuntu
aws_access_key_id: YOUR_ACCESS_KEY
aws_secret_access_key: YOUR_SECRET_KEY
aws_region: us-east-1
aws_ami_id: ami-f2c74d9a
aws_instance_type: t1.micro
aws_key_name: ec2_key
ansible_asg_app:
  port: 9001
  #hashes:
  #  38999b626d44e9550023e317f647c0bc: worker.yml
```

Example Playbook
----------------

See the example section. 

```
ansible-playbook -i example/inventory example/playbooks/create.yml
```

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
