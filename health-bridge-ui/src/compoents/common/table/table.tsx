import { ReactNode } from "react";
import { Table } from "reactstrap";

export interface IColumnSpec<T> {
    name: string;
    width?: string;
    cell: (row: T, i: number) => ReactNode;
}