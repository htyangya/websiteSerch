import xml.etree.ElementTree as ElementTree


class XmlReader:
    def __init__(self, fileName):
        self.fileName = fileName
        self.headerColumnList = []
        self.columnList = []

    def getHeaderColumnList(self):
        return self.headerColumnList

    def getColumnList(self):
        return self.columnList

    def read(self):
        self.headerColumnList = []
        self.columnList = []
        # XMLファイルを解析
        tree = ElementTree.parse(self.fileName)
        # XMLを取得
        root = tree.getroot()
        # 要素「head」のデータを1つずつ取得
        for heads in root.iter('head'):
            if heads is not None:
                for contents in heads.iter('contents'):
                    if contents is not None:
                        for column in contents.iter('column'):
                            self.headerColumnList.append(column.text)

        # 要素「body」のデータを1つずつ取得
        for bodys in root.iter('body'):
            if bodys is not None:
                for contents in bodys.iter('contents'):
                    if contents is not None:
                        for column in contents.iter('column'):
                            self.columnList.append(column.text)
