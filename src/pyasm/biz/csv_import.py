###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ["CsvParser", "AsciiEncodeException"]

import csv, os
from pyasm.common import Common

class AsciiEncodeException(Exception):
    pass

class CsvParser(object):

    def __init__(self, file_path):
        self.file_path = file_path

        if not os.path.exists(file_path):
            raise Exception("Path '%s' does not exists")

        self.num_rows_to_read = 0
        self.has_title_row = True
        self.lowercase_title = False
        self.titles = []
        self.data = []
        self.encoder = None


    def get_titles(self):
        return self.titles

    def get_data(self):
        return self.data

    def set_num_rows_to_read(self, num_rows):
        self.num_rows_to_read = num_rows

    def set_has_title_row(self, has_title_row):
        self.has_title_row = has_title_row

    def set_lowercase_title(self, lowercase):
        self.lowercase_title = lowercase

    def set_encoder(self, encoder):
        self.encoder = encoder

    def unicode_csv_reader(self, unicode_csv_data, dialect=csv.excel, encoder='utf-8', **kwargs):
        # csv.py doesn't do Unicode; encode as UTF-8 if explicitly set
        def utf_8_encoder(unicode_csv_data, encoder='utf-8'):
            # use this only if the file has been encoded in utf-8            
            if encoder:
                import codecs
                reader = codecs.getreader(encoder)(unicode_csv_data)
                line = reader.next()
                while line:
                    #ncr = Common.process_unicode_string(line)
                    encoded = line.encode(encoder)
                    yield encoded
                    line = reader.next()
            else: 
                for idx, line in enumerate(unicode_csv_data):
                    #ncr = Common.process_unicode_string(line)
                    # If no encoder is specified, test out the default ASCII
                    try:
                        line = line.encode('ASCII')
                    except:
                        raise AsciiEncodeException('Cannot encode [%s] in ASCII at line %s'%(line, idx+1))
                    
                    yield line
        
        csv_reader = csv.reader(utf_8_encoder(unicode_csv_data, encoder=encoder),
                                dialect=dialect, **kwargs)
        if encoder:
            for row in csv_reader:
                yield [unicode(cell, encoder) for cell in row]
        else:
            for row in csv_reader:
                yield row
        #return csv_reader
    
    def parse(self):

        input_file = open(self.file_path, 'rU') 
        csvreader = self.unicode_csv_reader(input_file, encoder=self.encoder)

        for row_count, row in enumerate(csvreader):
            # parse title: all titles must be filled
            if self.has_title_row and not self.titles:
                self.titles = []
                for cell in row:
                    if not cell:
                        continue
                    if self.lowercase_title:
                        cell = cell.lower()
                    self.titles.append( cell.strip() )
                if self.titles:
                    title_processed = True

            else:

                # parse the data 
                sobject = None

                # check if there any values in the row.  If not, skip the row
                values_in_row = False
                for cell in row:
                    if cell:
                        values_in_row = True
                        break
                if not values_in_row:
                    continue

                self.data.append(row)

            if self.num_rows_to_read and row_count == self.num_rows_to_read:
                break

        if self.data and not self.titles:
            for i in range(0, len(self.data[0]) ):
                self.titles.append("")

        input_file.close()

if __name__ == '__main__':
    import tacticenv
    from pyasm.security import Batch
    batch = Batch(login_code='admin')
    parser = CsvParser('/home/apache/data.csv')
    parser.set_encoder('utf-8')
    parser.parse()
    data = parser.get_data()
    print data


