from io import BytesIO
from pathlib import Path
from typing import Callable, Optional, Union
from base64 import b64decode

import dash_bootstrap_components as dbc
import odm_sharing.sharing as sh
import pandas as pd
import zipfile as zf
from dash import (
    Input,
    Output,
    State,
    dcc,
    html,
    no_update,
)
from dash.development.base_component import Component
from functional import seq
from odm_sharing.private.cons import CsvFile
from odm_sharing.private.utils import gen_output_filename

import stores
import utils
from components import modals
from dialogs.common import register_dialog_flag_callback

sharing_errors = dbc.Alert('', color='danger', is_open=False)

dataset_name = html.Span(id='dataset-name')
schema_name = html.Span(id='schema-name')
valid_status = html.Span(id='valid-status')
share_status = html.Span(id='share-status')

close_btn = dbc.Button('Close')
share_btn = dbc.Button('Share')

_schema_uploader = dcc.Upload(
    children=html.A('Upload'),
    className='schema-uploader',
    accept='.csv',
)

_dataset_downloader = dcc.Download()

_share_dialog = modals.init_modal(
    id='share-dialog',
    title='Share',
    body=[
        sharing_errors,
        html.Div([
            html.Strong('Dataset: '),
            dataset_name,
        ]),
        html.Div([
            html.Strong('Valid: '),
            valid_status,
        ]),
        html.Div([
            html.Strong('Schema: '),
            schema_name,
            _schema_uploader
        ]),
        html.Div([
            html.Strong('Status: '),
            share_status,
        ]),
        _dataset_downloader,
    ],
    buttons=[
        share_btn,
        close_btn,
    ]
)

layout = _share_dialog


def gen_schema_name_text(schema_name: str) -> str:
    return schema_name + ' or ' if schema_name else ''


def errors_to_strings(e: Union[Exception, list[Exception]]) -> list[str]:
    '''nested error list to nested str list'''

    def inner(ee: Union[Exception, list[Exception]]) -> Union[str, list[str]]:
        if isinstance(e, Exception):
            val = e.args[0]
            if isinstance(val, list) and len(val) > 1:
                return inner(val)
            else:
                val = val[0] if isinstance(val, list) else val
                return str(val).replace('file-obj', '')
        return seq(e).map(inner).list()

    result = inner(e)
    return result if isinstance(result, list) else [result]


def errors_to_html(caption: str, e: Union[Exception, list[Exception]]
                   ) -> Component:
    return html.Div([
        html.Strong(caption + ': '),
        utils.gen_html_list(errors_to_strings(e)),
    ])


def register(app):  # type:ignore
    register_dialog_flag_callback(app, _share_dialog,
                                  stores.share_dialog_flag,
                                  stores.share_dialog_init)

    @app.callback(
        Output(stores.share_dialog_flag, 'data', allow_duplicate=True),
        Input(close_btn, 'n_clicks'),
    )
    def on_close_btn(n: int) -> bool:
        '''close dialog'''
        return False

    @app.callback(
        [
            Output(dataset_name, 'children'),
            Output(valid_status, 'children'),
            Output(schema_name, 'children', allow_duplicate=True),
            Output(sharing_errors, 'is_open', allow_duplicate=True),
            Output(share_status, 'children'),
            Output(share_btn, 'disabled', allow_duplicate=True),
        ],
        Input(stores.share_dialog_init, 'data'),
        State(stores.dataset_id, 'data'),
        State(stores.datasets, 'data'),
        State(stores.sharing_schema_filename, 'data'),
    )
    def on_dialog_init(
        signal: bool, dataset_id: str, datasets: dict, schema_name: str,
    ) -> tuple[str, str, str, bool, str, bool]:
        NO_YES = ('No', 'Yes')
        assert dataset_id
        ds = datasets[dataset_id]
        ds_name = ds['filename']
        valid = ds.get('valid', None)
        valid_text = 'N/A' if valid is None else NO_YES[valid]
        schema_name_text = gen_schema_name_text(schema_name)
        status = 'Not started'
        disabled = not bool(schema_name)
        return ds_name, valid_text, schema_name_text, False, status, disabled

    @app.callback(
        [
            Output(stores.sharing_schema_data, 'data'),
            Output(stores.sharing_schema_filename, 'data',
                   allow_duplicate=True),
            Output(schema_name, 'children', allow_duplicate=True),
            Output(share_btn, 'disabled', allow_duplicate=True),
            Output(_schema_uploader, 'filename'),
            Output(sharing_errors, 'is_open', allow_duplicate=True),
            Output(sharing_errors, 'children', allow_duplicate=True),
        ],
        Input(_schema_uploader, 'filename'),
        State(_schema_uploader, 'contents'),
    )
    def on_schema_uploaded(
        filename: str, contents: str,
    ) -> tuple[str, str, str, bool, str, bool, str]:
        if not contents:
            return no_update
        (content_type, content_data) = contents.split(',')
        schema = BytesIO(b64decode(content_data))
        schema_name_text = gen_schema_name_text(filename)

        errors: Optional[Exception] = None
        try:
            sh.parse(schema)
        except Exception as e:
            errors = e
        valid = not errors

        # XXX: uploader.filename is reset so that the uploader will trigger
        # again even if the same filename is reused.
        return (
            content_data if valid else no_update,
            filename if valid else '',
            schema_name_text,
            (not valid),
            '',
            (not valid),
            errors_to_html('Schema errors', errors) if errors else no_update,
        )

    @app.callback(
        [
            Output(share_status, 'children', allow_duplicate=True),
            Output(stores.share_dialog_share, 'data'),
        ],
        Input(share_btn, 'n_clicks'),
    )
    def on_share(n: int) -> tuple[str, bool]:
        '''initializes the sharing status and signals for sharing to start'''
        # XXX: status must be initialized here since calling `set_progress` in
        # the beginning of the background-callback below isn't synced before
        # the process starts
        return (
            'Processing...',
            True,
        )

    @app.callback(
        output=[
            Output(_dataset_downloader, 'data'),
            Output(sharing_errors, 'is_open', allow_duplicate=True),
            Output(sharing_errors, 'children', allow_duplicate=True),
        ],
        inputs=[
            Input(stores.share_dialog_share, 'data'),
            State(stores.dataset_id, 'data'),
            State(stores.dataset_data, 'data'),
            State(stores.sharing_schema_filename, 'data'),
            State(stores.sharing_schema_data, 'data'),
        ],
        background=True,
        running=(Output(share_btn, 'disabled'), False, True),
        cancel=Input(close_btn, 'n_clicks'),
        progress=Output(share_status, 'children'),
        manager=stores.background_callback_manager,
        prevent_initial_call=True,
    )
    def on_share_signal(
        set_progress: Callable,
        n: int,
        dataset_id: str,
        dataset_data: dict,
        schema_filename: str,
        schema_data: str,
     ) -> tuple[dict, bool, Component]:
        '''runs the sharing function'''

        # get schema
        schema = BytesIO(b64decode(schema_data))
        schema_name = Path(schema_filename).stem

        # get data sources
        table_files = stores._decode_files(dataset_data[dataset_id])
        csv_files: list[CsvFile] = \
            [CsvFile(table=t, file=f) for t, f in table_files.items()]

        # extract filtered data
        try:
            org_dfs = sh.extract(schema, csv_files)
        except Exception as e:
            set_progress('Failed')
            return (
                no_update,
                True,
                errors_to_html('Sharing errors', e),
            )

        def write_dfs_to_excel_file(dfs: dict, outfile: BytesIO) -> None:
            with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
                for table, df in dfs.items():
                    df.to_excel(writer, sheet_name=table)

        # write excel/zip output file
        input_name = Path(dataset_id).stem
        outfile = BytesIO()
        file_count = len(org_dfs)
        if file_count == 0:
            set_progress('Failed')
            return (
                no_update,
                True,
                errors_to_html('Sharing errors', Exception('No data')),
            )
        elif file_count == 1:
            org = next(iter(org_dfs.keys()))
            dfs = org_dfs[org]
            write_dfs_to_excel_file(dfs, outfile)
            outfile_name = gen_output_filename(input_name, schema_name, org,
                                               '', 'xlsx')
            outfile_type = 'application/' +\
                'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            with zf.ZipFile(outfile, 'w', zf.ZIP_DEFLATED) as archive:
                for kv in org_dfs.items():
                    org, dfs = kv
                    xlfile = BytesIO()
                    write_dfs_to_excel_file(dfs, xlfile)
                    fn = gen_output_filename(input_name, schema_name, org, '',
                                             'xlsx')
                    archive.writestr(fn, xlfile.getvalue())
            outfile_name = f'{input_name}-{schema_name}.zip'
            outfile_type = 'application/zip'

        # download file
        set_progress('Finished')
        return (
            dcc.send_bytes(outfile.getvalue(), outfile_name, outfile_type),
            no_update,
            no_update,
        )
