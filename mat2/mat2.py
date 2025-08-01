
import os
import shutil
from typing import Tuple, List, Union, Set
import sys
import mimetypes
import argparse
import logging
import unicodedata
import concurrent.futures
from PIL.ExifTags import GPSTAGS, TAGS
import numpy
import pprint
from libmat2 import parser_factory
from libmat2 import check_dependencies, UnknownMemberPolicy

try:
    print("")
except ValueError as e:
    print(e)
    sys.exit(1)

__version__ = '0.9.0'

# Make pyflakes happy
assert Set
assert Tuple
assert Union

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)


def __check_file(filename: str, mode: int = os.R_OK) -> bool:
    if not os.path.exists(filename):
        print("[-] %s doesn't exist." % filename)
        return False
    elif not os.path.isfile(filename):
        print("[-] %s is not a regular file." % filename)
        return False
    elif not os.access(filename, mode):
        mode_str = []  # type: List[str]
        if mode & os.R_OK:
            mode_str += 'readable'
        if mode & os.W_OK:
            mode_str += 'writeable'
        print("[-] %s is not %s." % (filename, 'nor '.join(mode_str)))
        return False
    return True


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Metadata anonymisation toolkit 2')

    parser.add_argument('-V', '--verbose', action='store_true',
                        help='show more verbose status information')
    parser.add_argument('--unknown-members', metavar='policy', default='abort',
                        help='how to handle unknown members of archive-style '
                        'files (policy should be one of: %s) [Default: abort]' %
                        ', '.join(p.value for p in UnknownMemberPolicy))
    parser.add_argument('--inplace', action='store_true',
                        help='clean in place, without backup')
    parser.add_argument('--no-sandbox', dest='sandbox', action='store_true',
                        default=False, help='Disable bubblewrap\'s sandboxing.')
# 
    excl_group = parser.add_mutually_exclusive_group()
    excl_group.add_argument('files', nargs='*', help='the files to process',
                            default=[])
    excl_group.add_argument('-v', '--version', action='version',
                            version='MAT2 %s' % __version__)
    excl_group.add_argument('-l', '--list', action='store_true', default=False,
                            help='list all supported fileformats')
    excl_group.add_argument('--check-dependencies', action='store_true',
                            default=False,
                            help='check if MAT2 has all the dependencies it '
                            'needs')

    excl_group = parser.add_mutually_exclusive_group()
    excl_group.add_argument('-L', '--lightweight', action='store_true',
                            help='remove SOME metadata')
    excl_group.add_argument('-s', '--show', action='store_true',
                            help='list harmful metadata detectable by MAT2 '
                            'without removing them')

    return parser


def show_meta(filename: str, sandbox: bool, userInput: int):
    if not __check_file(filename):
        return

    p, mtype = parser_factory.get_parser(filename)  # type: ignore
    if p is None:
        print("[-] %s's format (%s) is not supported" % (filename, mtype))
        return
    p.sandbox = sandbox
    __print_meta(filename, p.get_meta(), userInput)


def __print_meta(filename: str, metadata: dict, userInput: int, depth: int = 1, ):
    padding = " " * depth*2
    if not metadata:
        print(padding + "No metadata found in %s." % filename)
        return

    print("[%s] Metadata for %s:" % ('+'*depth, filename))

    for (k, v) in sorted(metadata.items()):
        if isinstance(v, dict):
            __print_meta(k, v, depth+1, userInput)
            continue

        # Remove control characters
        # We might use 'Cc' instead of 'C', but better safe than sorry
        # https://www.unicode.org/reports/tr44/#GC_Values_Table
        try:
            v = ''.join(ch for ch in v if not unicodedata.category(ch).startswith('C'))
        except TypeError:
            pass  # for things that aren't iterable

        try:  # FIXME this is ugly.
            # print(padding + "  %s: %s" % (k, v))
            # print("",k, v)

            # print(k)

            if (userInput == 1 and k not in {"GPSPosition", "GPSAltitude", "GPSAltitudeRef", "GPSLatitude", "GPSLatitudeRef","GPSLongitude","GPSLongitudeRef"}):
                print("============================================================")
                print(" " ,k,v)
                print("============================================================")
            if (userInput == 2 and k in {"GPSPosition", "GPSAltitude", "GPSAltitudeRef", "GPSLatitude", "GPSLatitudeRef","GPSLongitude","GPSLongitudeRef"}):
                print("" , k,v)
                print("============================================================")
            if (userInput == 3 and k in {"MCCData", "Make","Model","ProfileCopyright"}): 
                print("" , k,v)
                print("============================================================")
            if (userInput == 4 and k in {"MCCData"}): 
                # print("Removing these values: MCCData")
                remove_some(["MCCData"],metadata)
                pprint.pprint(metadata)
                print("============================================================")
            if (userInput == 5 and k in {"Make"}): 
                print("Removing these values: Make")
                remove_some(["Make"],metadata)
                pprint.pprint(metadata)
                print("============================================================")
            if (userInput == 6): 
                remove_some(["Model","DeviceModel"],metadata)
                pprint.pprint(metadata)
                # print("", k,v)

        except UnicodeEncodeError:
            print(padding + "  %s: harmful content" % k)

    
    # print(" ", metadata)
    # pprint.pprint(metadata)

def clean_meta(filename: str, is_lightweight: bool, inplace: bool, sandbox: bool,
               policy: UnknownMemberPolicy) -> bool:
    mode = (os.R_OK | os.W_OK) if inplace else os.R_OK
    if not __check_file(filename, mode):
        return False

    p, mtype = parser_factory.get_parser(filename)  # type: ignore
    if p is None:
        print("[-] %s's format (%s) is not supported" % (filename, mtype))
        return False
    p.unknown_member_policy = policy
    p.lightweight_cleaning = is_lightweight
    p.sandbox = sandbox

    try:
        logging.debug('Cleaning %s…', filename)
        ret = p.remove_all()
        # ret = p.remove_some(True)

        if ret is True:
            shutil.copymode(filename, p.output_filename)
            if inplace is True:
                os.rename(p.output_filename, filename)
        return ret
    except RuntimeError as e:
        print("[-] %s can't be cleaned: %s" % (filename, e))
    return False


def show_parsers():
    print('[+] Supported formats:')
    formats = set()  # Set[str]
    for parser in parser_factory._get_parsers():  # type: ignore
        for mtype in parser.mimetypes:
            extensions = set()  # Set[str]
            for extension in mimetypes.guess_all_extensions(mtype):
                if extension not in UNSUPPORTED_EXTENSIONS:
                    extensions.add(extension)
            if not extensions:
                # we're not supporting a single extension in the current
                # mimetype, so there is not point in showing the mimetype at all
                continue
            formats.add('  - %s (%s)' % (mtype, ', '.join(extensions)))
    print('\n'.join(sorted(formats)))


def __get_files_recursively(files: List[str]) -> List[str]:
    ret = set()  # type: Set[str]
    for f in files:
        if os.path.isdir(f):
            for path, _, _files in os.walk(f):
                for _f in _files:
                    fname = os.path.join(path, _f)
                    if __check_file(fname):
                        ret.add(fname)
        elif __check_file(f):
            ret.add(f)
    return list(ret)


def main() -> int:
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.files:
        if args.list:
            show_parsers()
            return 0
        elif args.check_dependencies:
            print("Dependencies for MAT2 %s:" % __version__)
            for key, value in sorted(check_dependencies().items()):
                print('- %s: %s %s' % (key, 'yes' if value['found'] else 'no',
                                       '(optional)' if not value['required'] else ''))
        else:
            arg_parser.print_help()
        return 0

    elif args.show:
        for f in __get_files_recursively(args.files):
            show_meta(f, args.sandbox)
        return 0

    else:
        inplace = args.inplace
        policy = UnknownMemberPolicy(args.unknown_members)
        if policy == UnknownMemberPolicy.KEEP:
            logging.warning('Keeping unknown member files may leak metadata in the resulting file!')

        no_failure = True
        files = __get_files_recursively(args.files)
        # We have to use Processes instead of Threads, since
        # we're using tempfile.mkdtemp, which isn't thread-safe.
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = list()
            for f in files:
                future = executor.submit(clean_meta, f, args.lightweight,
                                         inplace, args.sandbox, policy)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                no_failure &= future.result()
        return 0 if no_failure is True else -1


if __name__ == '__main__':
    sys.exit(main())


# def remove_some(removed_values:List[str],metadata: dict):

#     for i in removed_values:
#         if i in metadata:
#             # print(f"{i}: {metadata[i]}") 
#             del(i)
#         else:
#             print("uh oh")

def remove_some(removed_values:List[str],metadata: dict):

    for i in removed_values:
        if i in metadata:
            del metadata[i]
        # else:
            # print("uh oh")
       

       
        # if removed_values in metadata:

        #     # print ("somethings happening")
        #     print (removed_values)
        #     # break
        
    
    # else: 
    #     print("Something went wrong...")
