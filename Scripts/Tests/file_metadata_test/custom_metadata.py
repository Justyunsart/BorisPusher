"""
Is it possible to add custom metadata to a file upon creation?
And is it possible to read/parse dirs based on this custom attribute?

The results are as expected; it totally works.
"""
import xattr


"""
Create a file with an additional hard coded attribute
"""
def create_cust_attr_file():
    with open("file.txt", 'w') as f:
        xattr.setxattr(f, 'user.cust_name', b'bowser')

def read_cust_attr_file():
    attr_val = xattr.getxattr("file.txt", 'user.cust_name').decode()
    print(attr_val)

if __name__ == "__main__":
    create_cust_attr_file()
    read_cust_attr_file()