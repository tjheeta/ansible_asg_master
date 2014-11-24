#!/usr/bin/env python

import time
import BaseHTTPServer
import boto
import boto.ec2
import pprint
from urlparse import urlparse
import ansible.playbook
from ansible import callbacks
from ansible import utils
import os, sys
import yaml

pp = pprint.PrettyPrinter(indent=4)

with open('hashes.yml') as f: 
    hashes=yaml.load(f)
with open('config.yml') as f: 
    config=yaml.load(f)
    if not 'port' in config or not 'region' in config or not 'playbook_path' in config:
      print "Configuration incorrect. Need to specify the port, aws region, and playbook path"
      sys.exit

HOST_NAME = '0.0.0.0'
PORT_NUMBER = config['port']

#print boto.ec2.get_all_instances()
class APIHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def verify_ipaddress(self, ipaddress):
        conn = boto.ec2.connect_to_region(config['region'])
        reservations=conn.get_all_instances()
        instances = [i for r in reservations for i in r.instances]
        for i in instances:
            if i.private_ip_address == ipaddress:
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

    def api_asg(self):
        uri = urlparse(self.path)
        run_hash=os.path.basename(uri.path)
        if run_hash in hashes:
            #if self.verify_ipaddress("172.31.59.87"):
            host = self.client_address[0]
            playbook = hashes[run_hash]
            if self.verify_ipaddress(host):
                self.run_playbook(host, os.path.join(config['playbook_path'], playbook))
                self.send_response(200, hashes[run_hash])
            else:
                self.send_error(403, "Access Denied")
        else:
            self.send_error(404, "Not found")

    def do_GET(self):
        """Respond to a GET request."""
        pp.pprint(self.address_string())
        uri = urlparse(self.path)
        if uri.path.startswith("/api/asg/"):
            self.api_asg()
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
