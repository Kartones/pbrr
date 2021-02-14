from pbrr.pbrr import PBRR

if __name__ == "__main__":
    reader = PBRR(data_path="feeds", opml_filename="subscriptions.xml")
    reader.run()
