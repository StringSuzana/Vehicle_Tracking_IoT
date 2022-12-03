import json


class AvlIds:
    def __init__(self):
        self.avl_data = self.loadData()

    @staticmethod
    def loadData():
        with open('avlIds.json') as f:
            data = json.load(f)
        return data

    def getAvlInfo(self, avl_id):
        try:
            avl_info = self.avl_data[avl_id]
            return avl_info
        except:
            print("Avl entry not found")
            return -1

    def idToAvl(self, data):
        result = {}
        for i in data:
            n_data = data[i]
            if n_data == "triggered_event":
                result["triggered_event"] = self.getAvlInfo(str(i))['name']
            else:
                for j in n_data:
                    id = str(j)
                    id_name = self.getAvlInfo(id)['name']
                    value = n_data[j]
                    result[id_name] = value
        return result


if __name__ == "__main__":
    avl = AvlIds()
    print(avl.getAvlInfo("72")['name'])
