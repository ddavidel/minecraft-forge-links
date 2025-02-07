"""
Retrieves the latest forge versions from the forge website and
saves them to the version_list.json file.
"""

import json
import requests
from bs4 import BeautifulSoup

FILENAME = "version_list.json"

base_url = "https://files.minecraftforge.net/net/minecraftforge/forge/"


def get_forge_versions():
    """
    Does all the work.
    """
    response = requests.get(base_url, timeout=10)
    response.raise_for_status()  # ensure the request was successful
    soup = BeautifulSoup(response.text, "html.parser")

    data_dict = {}

    page_links = soup.select("div a[href*='index']")

    # Active version
    on_page_version = soup.select("li.elem-active")
    for version in on_page_version:
        version = version.text.strip()
        sub_versions = soup.select("a[href*='maven']")
        for subver in sub_versions:
            if not subver.get("title") == "Direct Download":
                continue

            direct_download_url = subver.get("href")
            if not ".jar" in direct_download_url or "universal" in direct_download_url:
                continue

            forge_version = None

            for sect in subver.get("href").split("/"):
                if (
                    forge_version is not None
                    or not sect.replace(".", "").replace("-", "").isnumeric()
                ):
                    continue

                forge_version = sect

            if forge_version is None:
                continue

            data_dict[forge_version] = direct_download_url

    for link in page_links:
        version = link.text.strip()
        if version == "Project Index":
            continue

        page_url = base_url + link.get("href")
        version_response = requests.get(page_url, timeout=10)
        version_response.raise_for_status()
        version_soup = BeautifulSoup(version_response.text, "html.parser")

        # subversion_download = version_soup.select("a[href*='adfoc']")
        subversion_download = version_soup.select("a[href*='maven']")
        for subver in subversion_download:
            if not subver.get("title") == "Direct Download":
                continue

            direct_download_url = subver.get("href")
            if not ".jar" in direct_download_url or "universal" in direct_download_url:
                continue

            forge_version = None

            for sect in subver.get("href").split("/"):
                if (
                    forge_version is not None
                    or not sect.replace(".", "").replace("-", "").isnumeric()
                ):
                    continue

                forge_version = sect

            if forge_version is None:
                continue

            data_dict[forge_version] = direct_download_url

    return data_dict


print("Getting forge versions... This might take a while.")
forge_versions = get_forge_versions()
print("Finished getting forge versions.")

with open(FILENAME, "w", encoding="utf-8") as file:
    json.dump(forge_versions, file, indent=4)

print("Finished writing to file.")
