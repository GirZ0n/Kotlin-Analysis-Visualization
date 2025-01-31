from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

import streamlit as st


def get_prefix(fq_name: str, prefix_len: int) -> str:
    return '.'.join(fq_name.split('.')[:prefix_len])


def get_package(fq_name: str, packages: List[str]) -> str:
    max_package = ''
    for package in packages:
        if fq_name.startswith(package) and len(max_package) < len(package):
            max_package = package
    return 'other' if max_package == '' else max_package


def fq_names_group_by_packages_stats(fq_names: List[str], packages: List[str]) -> Dict[str, int]:
    fq_name_groups = defaultdict(int)
    for fq_name in fq_names:
        fq_name_groups[get_package(fq_name, packages)] += 1

    fq_name_groups.pop('other', None)
    return fq_name_groups


@st.cache
def read_from_csv(csv_path: Union[str, Path], column_name: str) -> List[str]:
    return list(map(str, pd.read_csv(csv_path, keep_default_na=False)[column_name]))


@st.cache
def get_fq_names_stats(
    fq_names_path: Union[str, Path],
    filter_packages_path: Optional[Union[str, Path]] = None,
    group_by_packages_path: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    fq_names = read_from_csv(fq_names_path, 'import')

    if filter_packages_path is not None:
        filter_package_names = read_from_csv(filter_packages_path, 'package_name')
        fq_names = [
            fq_name for fq_name in fq_names if not any(fq_name.startswith(fp_name) for fp_name in filter_package_names)
        ]

    if group_by_packages_path is not None:
        package_names = read_from_csv(group_by_packages_path, 'package_name')
        fq_names_stats = fq_names_group_by_packages_stats(fq_names, package_names)
    else:
        fq_names_stats = Counter(fq_names)

    return pd.DataFrame(fq_names_stats.items(), columns=['fq_name', 'count'])
