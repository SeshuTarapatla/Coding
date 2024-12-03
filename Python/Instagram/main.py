# create a oneplus u2 device
# read profile details: title, followers, following
# take a screenshot
# download profile picture
# combine both and save
from os import system
from instagram import Instagram

    
def main():
    system("python clean_scanned.py")
    Instagram().execute()
    system("python backup.py")


if __name__ == "__main__":
    main()