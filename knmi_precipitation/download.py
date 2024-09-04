import requests

from datetime import datetime
from pathlib import Path


class OpenDataAPI:
    def __init__(self, api_token):
        self.base_url = "https://api.dataplatform.knmi.nl/open-data/v1"
        self.dataset_name = "radar_forecast"
        self.headers = {"Authorization": api_token}

    def __get_data(self, url, params=None):
        return requests.get(url, headers=self.headers, params=params).json()

    def download_latest_file(self, file_path=None, after=None):
        latest_file_info = self.get_latest_file_info()
        file_url = self.get_file_url(latest_file_info["filename"])

        file_date = datetime.fromisoformat(latest_file_info["created"])
        if after is not None and file_date <= after:
            return None

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        file_full_path = path / latest_file_info["filename"]

        self.download_file_from_temporary_download_url(
            file_url["temporaryDownloadUrl"], file_full_path
        )

        return file_full_path

    def get_latest_file_info(self):
        params = {"maxKeys": 1, "orderBy": "created", "sorting": "desc"}
        files = self.list_files(params)
        return files["files"][0]

    def list_files(self, params):
        return self.__get_data(
            f"{self.base_url}/datasets/radar_forecast/versions/2.0/files",
            params=params,
        )

    def get_file_url(self, file_name):
        return self.__get_data(
            f"{self.base_url}/datasets/radar_forecast/versions/2.0/files/{file_name}/url"
        )

    def download_file_from_temporary_download_url(self, download_url, filename):
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception:
            raise Exception("Unable to download file using download URL")
