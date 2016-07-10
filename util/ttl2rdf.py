import sys
import os
import pathlib
from subprocess import call

""""
usage: python3 ttl2rdf.py <path> <output>

trasveral all ttl in the <path>,
    transform it into rdf format 
    save it in the <output>, while keeping the sub directory structure in the <path>
"""

ttl2rdf_jar = "/Users/tdong/git/DAM/util/rdf2rdf-1.0.1-2.3.1.jar"

def replace_path_head(path0, head1, head2):
    '''
    head1 is the head of path0
    replace head2 with head1
    '''
    return os.path.join(head2, *pathlib.Path(path0).parts[len(pathlib.Path(head1).parts)-1:])

def ttl2rdf(inpath, outpath):
    for root, dirs, fnlst in os.walk(inpath):
        for fn in fnlst: 
            fn0, ext = os.path.splitext(fn)
            if ext=='.ttl':
                inputfile = os.path.join(root, fn) 
                outputfile = os.path.join(outpath, *pathlib.Path(root).parts[len(pathlib.Path(inpath).parts)-1:], fn0+'.rdf')
                if not os.path.exists(os.path.dirname(outputfile)):
                    try:            
                        os.makedirs(os.path.dirname(outputfile))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                ofile = open(outputfile, 'w+')
                print(inputfile)
                print(outputfile)
                print('--')
                call(["java", "-jar", ttl2rdf_jar, inputfile, outputfile])
                ofile.close()
        


if __name__ == "__main__":
    if (len(sys.argv) !=3):
        print("Usages: python3 ttl2rdf.py <path> <output>")
    else:
        ttl2rdf(sys.argv[1], sys.argv[2])