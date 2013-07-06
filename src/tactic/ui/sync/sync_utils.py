############################################################
#
#    Copyright (c) 2011, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['SyncUtils']


import tacticenv

from pyasm.common import Environment, Xml, TacticException
from pyasm.biz import Project
from pyasm.search import SearchType, Search

import os, codecs


class SyncUtils(object):

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        # NOTE: this search key is to find the server, not the transactions
        search_key = my.kwargs.get("search_key")
        if not search_key:
            server_code = my.kwargs.get("server_code")
            my.server_sobj = Search.get_by_code("sthpw/sync_server", server_code)
        else:
            my.server_sobj = Search.get_by_search_key(search_key)


        my.start_expr = my.kwargs.get("start_expr")
       

    def get_server_sobj(my):
        return my.server_sobj

    def get_remote_host(my):
        return my.server_sobj.get_value("host")


    def get_remote_server(my):
        if not my.server_sobj:
            return


        host = my.server_sobj.get_value("host")
        ticket = my.server_sobj.get_value("ticket")

        # connect to the admin project? This likely does not matter
        project_code = 'admin'

        # get the transaction log of a remote server
        from tactic_client_lib import TacticServerStub
        remote_server = TacticServerStub(
            protocol='xmlrpc',
            server=host,
            project=project_code,
            ticket=ticket,
        )

        return remote_server


    def get_date(my, expr):

        from dateutil import parser, relativedelta
        from datetime import datetime

        now = datetime.now()

        parts = expr.split(" ")
        if parts[1] in ['hour', 'hours']:
            num = int(parts[0])
            date = now - relativedelta.relativedelta(hours=num)
        elif parts[1] in ['day', 'days']:
            num = int(parts[0])
            date = now - relativedelta.relativedelta(days=num)
        elif parts[1] in ['week', 'weeks']:
            num = int(parts[0])
            date = now - relativedelta.relativedelta(weeks=num)
        elif parts[1] in ['month', 'months']:
            num = int(parts[0])
            date = now - relativedelta.relativedelta(months=num)
        elif parts[1] in ['year', 'years']:
            num = int(parts[0])
            date = now - relativedelta.relativedelta(years=num)
        else:
            date = now

        return date


    def get_transaction_info(my):

        remote_server = my.get_remote_server()

        
        search_keys = my.kwargs.get("search_keys")

        project_code = my.kwargs.get("project_code")
        if not project_code:
            project_code = Project.get_project_code()

        print "search_keys: ", search_keys

        if search_keys:
            search_keys_str = "|".join(search_keys)
            # need to get the code from the search_keys
            codes = []
            for search_key in search_keys:
                # HACK
                parts = search_key.split("code=")
                code = parts[1]
                codes.append(code)
            codes_str = "|".join(codes)

            filters = [
                ['code','in',codes_str]
            ]
            remote_codes = remote_server.query("sthpw/transaction_log", filters=filters, columns=['code'], order_bys=['timestamp'])

        elif my.start_expr:

            start_date = my.get_date(my.start_expr)

            # FIXME: this only works with Postgres
            filters = [
	        ['timestamp', '>', str(start_date)],
            ]

            if project_code:
                filters.append( ['namespace', project_code] )

            remote_codes = remote_server.query("sthpw/transaction_log", filters=filters, columns=['code'], order_bys=['timestamp'])
        else:
            raise TacticException("No start date expression given")


        print "# remote codes: ", len(remote_codes)



        # get all of the local transactions with the same filters
        search = Search("sthpw/transaction_log")
        search.add_column("code")
        search.add_filter("namespace", project_code)
        search.add_op_filters(filters)
        search.add_order_by("timestamp")
        print "search: ", search.get_statement()
        local_codes = search.get_sobjects()
        print "local codes: ", local_codes

        lset = set()
        for lt in local_codes:
            lcode = lt.get_value("code")
            if not lcode:
                continue
            lset.add(lcode)
            

        rset = set()
        for rt in remote_codes:
            rcode = rt.get("code")
            if not rcode:
                continue
            rset.add(rcode)
            

        info = {}
        remote_diff = rset.difference(lset)
        local_diff = lset.difference(rset)

        # go get the missing remote transactions
        filters = [['code', 'in', "|".join(remote_diff)]]
        remote_transactions = remote_server.query("sthpw/transaction_log", filters=filters, order_bys=['timestamp'])
        for i, transaction in enumerate(remote_transactions):
            sobject = SearchType.create("sthpw/transaction_log")
            sobject.data = transaction
            remote_transactions[i] = sobject
        info['remote_transactions'] = remote_transactions
 

        search = Search("sthpw/transaction_log")
        search.add_filters("code", local_diff)
        search.add_order_by("timestamp")
        local_transactions = search.get_sobjects()
        info['local_transactions'] = local_transactions

        local_paths = []
        for transaction in local_transactions:
            paths = my.get_file_paths(transaction)
            if not paths:
                continue
            local_paths.extend(paths)
        info['local_paths'] = local_paths


        remote_paths = [] 
        for transaction in remote_transactions:
            paths = my.get_file_paths(transaction)
            if not paths:
                continue
            remote_paths.extend(paths)
        info['remote_paths'] = remote_paths


        return info



    def get_file_paths(my, transaction, mode='lib'):

        transaction_xml = transaction.get_xml_value("transaction")
        if not transaction_xml:
            return []

        from pyasm.common import Xml, Environment

        if isinstance(transaction_xml, basestring):
            xml = Xml()
            xml.read_string(transaction_xml)
        else:
            xml = transaction_xml


        base_dir = Environment.get_asset_dir()
        paths = []


        # get all of the file nodes
        nodes = xml.get_nodes("transaction/file")
        for node in nodes:

            if xml.get_attribute(node, "type") == 'create':
                src = xml.get_attribute(node, "src")

                if mode == 'relative':
                    path = src
                else:
                    path = "%s/%s" % (base_dir, src)
                paths.append(path)

        return paths





    """
    def sync_remote_transactions(my):

        print "executing missing transactions locally: ", len(missing_transactions)
        # execute missing transactions on the local machine
        for transaction in missing_transactions:
            cmd = RunTransactionCmd(transaction_xml=transaction)
            cmd.execute()
    """


