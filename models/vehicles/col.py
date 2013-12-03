import sys
of=file(sys.argv[1][0:-4]+"col.egg","w")
for line in file(sys.argv[1]): # read the file line by line
    of.write(line)
    if line.find("<Group>")!=-1:
        of.write("  <Collide> { Polyset keep descend }\n") # add the line you want