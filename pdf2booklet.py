#!/bin/python
""" A program to print a pdf as a booklet """
""" By Paulo De Tiege """

import argparse
from shutil import copy
from subprocess import run

try:
    from PyPDF2 import PdfWriter, PdfReader
except ImportError:
    print('Error: PyPDF2 is not installed, yet is required.')
    exit()

class Pdf:
    def __init__(self,filename):
        self.input_filename = filename
        self.output_filename = 'output.pdf'
        
        # For safety, only work on a copy of the PDF
        copy(self.input_filename, self.output_filename)

    def has_correct_pagecount(self):
        """Check if the file has a pagecount that is a multiple of four."""

        reader = PdfReader(self.input_filename)
        number_of_pages = len(reader.pages)

        if number_of_pages % 4 == 0:
            return True
        else:
            return False

    def insert_blank_pages(self,has_back_cover):
        """Add blank pages until the pdf has a pagecount that is a multiple of four."""
       
        with open(self.input_filename, 'rb') as file:
            reader = PdfReader(file)

            # Pad the pdf with blank pages at the end
            with open(self.output_filename, 'wb') as output:
                writer = PdfWriter(output)

                for page in range(len(reader.pages)):
                    writer.add_page(reader.pages[page])

                while len(writer.pages) % 4 != 0:
                    #writer.add_blank_page()
                    if has_back_cover:
                        writer.insert_blank_page(index=len(reader.pages)-1)
                    else:
                        writer.add_blank_page()

                writer.write(output)

            writer.close()

    def print_list(self):
        """Pages from the back and front of the booklet are printed on the same page.
        For n pages, this becomes 1, n, n-1, 2, 3, n-2, n-3, 4, 5, etc.
        """

        reader = PdfReader(self.output_filename)
        
        print_order = []
        pages = []

        for i in range(1,len(reader.pages)+1):
            pages.append(i)

        while len(pages) > 0:
            print_order.append(pages.pop(0))
            print_order.append(pages.pop())
            print_order.append(pages.pop())
            print_order.append(pages.pop(0))

        return print_order

    def reorganize(self):
        """Reformat the PDF to already be in the correct order for booklet printing."""

        print_order = self.print_list()

        with open(self.output_filename, 'rb') as file:
            reader = PdfReader(file)
            writer = PdfWriter()

            for page in print_order:
                writer.add_page(reader.pages[page-1])

            with open(self.output_filename, 'wb') as output:
                writer.write(output)
            writer.close()
        return

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('filename', type=str, 
                        help='The filename of the pdf to be printer.')
    parser.add_argument('-l', '--list', dest='display_print_list', action='store_true',
                        help='Print a list of pagenumbers in the correct order for booklet printing.')
    parser.add_argument('-r', '--reorganize', dest='reorganize', action='store_true',
                        help='Reorganize the output pdf to be immediately printable in booklet format.')
    parser.add_argument('-b', '--backcover', dest='backcover', action='store_true',
                        help='Account for a back cover in the pdf.')
    parser.add_argument('-p', '--print', dest='also_print', action='store_true',
                        help='Also print immediately')

    args = parser.parse_args()

    input_pdf = Pdf(args.filename)
    print(f'Converting {input_pdf.input_filename} into booklet format.')

    # Regardless of whether the file has to be padded, an output pdf is expected
    if not input_pdf.has_correct_pagecount():
        print('-> PDF has too few pages. Padding with blank pages.')
        input_pdf.insert_blank_pages(args.backcover)
        print('--> Done.')

    if args.reorganize:
        print('-> Reorganizing PDF pages to booklet page order.')
        input_pdf.reorganize()
        print('--> Done.')

    if args.also_print:
        print('-> Sending file to printer.')
        command = ['lpr', '-o', 'sides=two-sided-short-edge', '-o','number-up=2', '-o','number-up-layout=rltb', input_pdf.output_filename]
        run(command)
        print('--> Done.')

    if args.display_print_list:
        print()
        print('The order to provide the printer is as follows:')
        for i,page_number in enumerate(input_pdf.print_list()):
            if i == len(input_pdf.print_list())-1:
                print(page_number)
            else:
                print(page_number, end=', ')

# If run as a program, process command-line arguments
if __name__ == '__main__':
    main()
