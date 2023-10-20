from enum import Enum
from typing import Dict, List, TypeAlias


ColumnName: TypeAlias = str
TableName: TypeAlias = str
VersionStr: TypeAlias = str
TableMetadata: TypeAlias = Dict[VersionStr, Dict[TableName, List[ColumnName]]]


class Version(Enum):
    V1_0_0 = 'v1.0.0'
    V1_1_0 = 'v1.1.0'
    V2_0_0 = 'v2.0.0'
