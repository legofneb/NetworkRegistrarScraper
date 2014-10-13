A Scraper for Network Registrar
===============================

This scrapes network registrar and generates a .csv file containing the IPAddress, Hostname, MAC Address, and status flags.
Much more useful in this report as the website, and much easier to use programmatically. 

Uses python3, requires BeautifulSoup4

You will need a config.ini file in this form:

    [User]
    id : your_network_registrar_id
    password: your_network_registrar_password

    [Website]
    rootUrl: https://network_registrar_path.yourCompany.com:port
