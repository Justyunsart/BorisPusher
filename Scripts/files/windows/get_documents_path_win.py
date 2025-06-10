
"""
Because the user can change the default location of their 'Documents' folder,
this is needed to get the path for windows users instead of using os.path.expanduser('~/Documents').

from: https://stackoverflow.com/questions/6227590/finding-the-users-my-documents-path
"""
def get_documents_path_win():
    import ctypes.wintypes
    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value

if __name__ == '__main__':
    print(get_documents_path_win())