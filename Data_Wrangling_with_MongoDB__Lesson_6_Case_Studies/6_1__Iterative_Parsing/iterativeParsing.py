import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        tagList = {}
        
        for event, element in ET.iterparse(filename):
            if (element.tag in tagList):
                tagList[element.tag] += 1;
            else:
                tagList[element.tag] = 1;
        return tagList

def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}

    

if __name__ == "__main__":
    test()
