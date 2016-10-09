import zipfile
import xml.etree.ElementTree as ElementTree

BoMEpub = zipfile.ZipFile("book-of-mormon-eng.epub")

# This is the standard TOC for an epub. The unzipper can give a list of files,
# but it'll list them alphabetically, which won't necessarily be in the right
# order according to the TOC.
tocFile = BoMEpub.read("OEBPS/toc.ncx")

# This "root" thing is the main item in the XML document. All the subsequent
# things are nested underneath it.
tocRoot = ElementTree.fromstring(tocFile)

# This "navMap" thing is the XML block which has the actual TOC in it. It
# It probably makes clickable links as well, but I'm not terribly worried about
# that...
tocNavMap = tocRoot[2]

# Extract the individual item paths from the navMap.
tocItems = [item[1].attrib["src"] for item in tocNavMap]

# Get the same XML roots for each individual item in the TOC.
tocItemsRoots = [ElementTree.fromstring(BoMEpub.read("OEBPS/%s"%item)) for item in tocItems]

bookFileList = []

for item in tocItemsRoots:
    if "chapter" in item[1].attrib["class"]:
        pass        
        #print("Chapter: {0}".format(item[1].attrib["class"][len("chapter") + 1:]))
    elif "book" in item[1].attrib["class"]:
        if "illustrations" not in item[1].attrib["class"]:
            #print("Book: {0}".format(item[1].attrib["class"][len("book") + 1:]))
            bookFileList.append(BoMEpub.read("OEBPS/{0}.xhtml".format(item[1].attrib["class"][len("book") + 1:])))
    else:
        pass

bookRootList = []
for file in bookFileList:
    bookRootList.append(ElementTree.fromstring(file))
    for child in bookRootList[-1][1][0]:
        print(child.attrib)         
        
#for item in nephiRoot.iter():
#    if str(item.text).strip() != "None":
#        print(item.text)
#    if item.tag[-1] == 'a':
#        print(item)