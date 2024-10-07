import { ReactNode } from "react";
import { Table } from "reactstrap";
import {
    RecoilState,
    RecoilValueReadOnly,
    useRecoilState,
    useRecoilValueLoadable,
  } from "recoil";

  
export interface ITableFilter<Filter> {
    page: number;
    pageSize: number;
    filter?: Filter;
  }

export interface IColumnSpec<T> {
    name: string;
    width?: string;
    cell: (row: T, i: number) => ReactNode;
}

export interface IRow {
    serialNumber?: number;
}


interface IProps<T, Filter> {
    activePage?: number;
    pageSize?: number;
    datasource?: RecoilValueReadOnly<FetchResponse<T[]>>;
    pagingStore?: RecoilState<PageParam>;
    setActivePage?: (page: number) => void;
    columns: IColumnSpec<T>[];
    hideSearch?: boolean;
    noPagination?: boolean;
    url?: string;
    postData?: Filter;
    data?: T[];
    subHeaderComponent?: ReactNode;
    subHeader?: boolean;
    title?: string;
  }
  
  function CustomTable<T, Filter>({
    columns,
    datasource,
    pagingStore,
    ...props
  }: IProps<T, Filter>) {
    const datasourceLoadable = useRecoilValueLoadable(
      datasource ?? emptyRecordState
    );
    const [paging, setPagingConfig] = useRecoilState(
      pagingStore ?? emptyPagingState
    );
  
    const getTableData = () => {
      if (props.data) return props.data;
  
      return (datasourceLoadable.contents?.data ?? []) as T[];
    };
  
    const renderEmptyRow = (text: string) => {
      return (
        <tbody>
          <tr>
            <td className="" colSpan={columns.length}>
              {text}
            </td>
          </tr>
        </tbody>
      );
    };
    const total =
      datasourceLoadable.contents?.total ??
      datasourceLoadable.contents?.data?.length;
    return (
      <div className="custom-table border">
        <Table striped>
          <thead>
            <tr>
              {columns.map((c) => {
                return <th key={c.name?.toString()}>{c.name}</th>;
              })}
            </tr>
          </thead>
          {datasourceLoadable.state == "loading" ? (
            renderEmptyRow("Loading...")
          ) : getTableData().length === 0 ? (
            renderEmptyRow("No Records")
          ) : (
            <tbody>
              {getTableData()?.map((r, i) => {
                return (
                  <tr key={`row${i}`}>
                    {columns.map((c, j) => {
                      return (
                        <td key={`col-${i}-${j}`} width={c.width ?? undefined}>
                          {c.cell?.(r, i)}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          )}
        </Table>
        {pagingStore && total > paging.limit && (
          <div className="d-flex flex-column align-items-center">
            <CustomPagination
              currentPage={paging.page}
              itemsPerPage={paging.limit}
              totalItems={total}
              onPageChange={(page) => {
                setPagingConfig((p) => ({
                  ...p,
                  page,
                  offset: p.limit * (page - 1),
                }));
              }}
            />
          </div>
        )}
      </div>
    );
  }
  
  export default CustomTable;