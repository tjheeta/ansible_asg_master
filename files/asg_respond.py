#!/usr/bin/env python

import time
import BaseHTTPServer
import boto
import boto.ec2
from urlparse import urlparse
import ansible.playbook
from ansible import callbacks
from ansible import utils
import os, sys
import yaml

def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v)) 
        for k, v in dictionary.items())

# setup the hashes if they exist
use_hashes = False
hashes_name = 'hashes.yml'
if os.path.isfile(hashes_name):
    use_hashes = True
    with open(hashes_name) as f:
        hashes=convert_keys_to_string(yaml.load(f))

with open('config.yml') as f:
    config=yaml.load(f)
    if not 'port' in config or not 'region' in config or not 'playbook_path' in config:
      print "Configuration incorrect. Need to specify the port, aws region, and playbook path"
      sys.exit

HOST_NAME = '0.0.0.0'
PORT_NUMBER = config['port']

#print boto.ec2.get_all_instances()
class APIHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def ec2_verify_ipaddress(self, ipaddress):
        conn = boto.ec2.connect_to_region(config['region'])
        reservations=conn.get_all_instances()
        instances = [i for r in reservations for i in r.instances]
        for i in instances:
            if i.private_ip_address == ipaddress:
                return True
            if i.ip_address == ipaddress:
                return True
        return False

    def run_playbook(self, host, playbook):
        """ Run a given playbook against a specific host, with the given username and private key file.  """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

        pb = ansible.playbook.PlayBook(
            host_list=[host,],
            playbook=playbook,
            forks=1,
            #remote_user=user,
            #private_key_file=key_file,
            runner_callbacks=runner_cb,
            callbacks=playbook_cb,
            stats=stats
            )
        pb.run()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def api_ec2_asg(self):
        uri = urlparse(self.path)
        current_hash=os.path.basename(uri.path) # /the/uri/$current_hash
        if use_hashes:
            if current_hash in hashes:
                playbook = os.path.join(config['playbook_path'], hashes[current_hash])
            else:
                self.send_error(404, "Not found")
                return False
        else:
            playbook = os.path.join(config['playbook_path'], current_hash)

        if not os.path.isfile(playbook):
            self.send_error(404, "Not found")
            return False

        host = self.client_address[0]
        if self.ec2_verify_ipaddress(host):
            self.send_response(200, playbook)
            self.run_playbook(host, playbook)
            return True
        else:
            self.send_error(403, "Access Denied")
            return True

    def do_GET(self):
        """Respond to a GET request."""
        uri = urlparse(self.path)
        if uri.path.startswith("/api/ec2/asg/"):
            self.api_ec2_asg()
        else:
            self.send_error(404, "Not found")


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), APIHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
