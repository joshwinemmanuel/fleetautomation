import pkg_resources

def list_installed_packages():
    """
    List installed versions of numpy and pandas.
    """
    installed_packages = pkg_resources.working_set
    numpy_version = None
    pandas_version = None
    for pkg in installed_packages:
        if pkg.key == 'numpy':
            numpy_version = pkg.version
        elif pkg.key == 'pandas':
            pandas_version = pkg.version
    return numpy_version, pandas_version

if __name__ == "__main__":
    numpy_version, pandas_version = list_installed_packages()
    print(f"numpy version: {numpy_version}")
    print(f"pandas version: {pandas_version}")
