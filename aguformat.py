import os, re

class input_replacer():
    def __init__(self, inbase='main', outbase='final', root=None, bibpattern=r"\\bibliography{[^}]*}{[0-9]*}"):
        self.maindottex = os.path.abspath(inbase+".tex")
        self.finaldottex = os.path.abspath(outbase+".tex")
        self.main = self.maindottex[:-4]
        if root:
            self.root = os.path.abspath(root)
        else:
            self.root = os.path.dirname(self.maindottex)
        self.bibpattern = bibpattern
        with open(self.maindottex,"r") as f:
            self.text = f.read()

    def reformat(self,
                 replace_inputs=True,
                 strip_comments=True,
                 clean_repeated_comments=True,
                 clean_lonely_comments = True,
                 insert_bibliography=True,
                 bold_vectors=True,
                 software_names=True,
                 no_dash=True,
                 scale_height_no_m=True,
                 no_glossary=True):
        text = self.text

        # replace \input{} statements with full text
        if replace_inputs:
            regex=re.compile(r"([^% ])\\input{([^}]*)}")
            text = regex.sub(self.replace_input_statement, text)
            regex=re.compile(r"([^% ])\\include{([^}]*)}")
            text = regex.sub(self.replace_input_statement, text)        
        
        # strip all comments, but not literal percent symbols
        if strip_comments:
            comment = re.compile(r"(?<!\\)%+.*\n")
            text = comment.sub(self.replace_comment, text)
            if clean_repeated_comments:
                text = re.sub(r"%(\n+%)+","%", text)
            if clean_lonely_comments:
                text = re.sub(r"\n%\n","\n", text)

        if insert_bibliography:
            self.bblfile = self.locate_bbl()
            regex = re.compile(self.bibpattern)
            text = regex.sub(self.bibreplace, text)

        if bold_vectors:
            vector = re.compile(r"(\\vec)")
            text = vector.sub(lambda m: r"\mathbf", text)

        if software_names:
            soft = re.compile(r"(\\texttt)")
            text = soft.sub(lambda m: r"\textsf", text)

        if no_dash:
            oii = re.compile(r"O-II")
            text = oii.sub(lambda m: r"OII", text)

        if scale_height_no_m:
            rx = re.compile(r"H_m")
            text = rx.sub(lambda m: r"H", text)

        if no_glossary:
            rx = re.compile(r"\\gls")
            text = rx.sub(lambda m: r"", text)
            rx = re.compile(r"\\renewcommand")
            text = rx.sub(lambda m: r"", text)
            
        # write the new .tex file
        with open(self.finaldottex,"w") as f:
            f.write(text)
        self.text = text

    def replace_input_statement(self,m):
        path = os.path.join(self.root,m.group(2))
        fname = path + ".tex"
        with open(fname,'r') as f:
            lines = f.readlines()
        return m.group(1)+"".join(lines)

    def replace_comment(self, m):
        """Replace comments with empty comments, so that they retain their newline-escaping abilities."""
        return '%\n'        

    def locate_bbl(self):
        bblfile = self.main + ".bbl"
        if os.path.isfile(bblfile):
            return os.path.abspath(bblfile)
        else:
            raise MissingBblError(bblfile)

    def bibreplace(self,m):
        with open(self.bblfile,"r") as f:
            bbltext = f.read()
        return bbltext    
    
class MissingBblError( BaseException ):
    """Exception for missing bibliography.
        bblfile = name of expected .bbl finaldottex
        msg = message to print 
    """
    def __init__(self,bblfile):
        self.bblfile = bblfile
        self.msg = "'{}' not found in {}".format(self.bblfile,__name__)

def main(infile,outfile):
    ir = input_replacer(infile, outfile)
    ir.reformat()

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Flatten TeX documents for publishing.')
    parser.add_argument('-i', '--in', dest='inname')
    parser.add_argument('-o', '--out', default='flattened', dest='outname')
    args = parser.parse_args()
    main(args.inname, args.outname)
