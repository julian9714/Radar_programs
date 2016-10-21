import ConfigParser

#path_prop = '/home/julian/Dropbox/Tesis/tesis_progs/Reproyecta_radar/'
#file_properties = 'reprojectradar_properties.ini'

class parsing_file(object):
    'Parsea un archivo. La clase recibe la ruta del archivo y el nombre .ini'
    def __init__(self, path_prop, file_properties):
        self.path_prop = path_prop
        self.file_properties = file_properties
    def get_parsingpar(self):
        self.fileradar_prop = ConfigParser.ConfigParser()
        self.fileradar_prop.read(self.path_prop+self.file_properties)
        self.sections = self.fileradar_prop.sections()
        self.dic_prop = {}
        for str_section in self.sections:
            self.in_prop = self.fileradar_prop.options(str_section)
            for name_inprop in self.in_prop:
                if (name_inprop ==  'range_bound') or (name_inprop == 'elev_bound'):
                    element_prop = self.fileradar_prop.getfloat(str_section, name_inprop)
                else:
                    element_prop = self.fileradar_prop.get(str_section, name_inprop)
                self.dic_prop.update({name_inprop:element_prop})
        return self.dic_prop
   
#test = parsing_file(path_prop, file_properties)
#in_prop = test.get_parsingpar()