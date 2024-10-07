import CustomTable, { IColumnSpec } from "./common/table/table";
import { pagingState, segmentsSelector } from "../store/health-talk-store";
import { HealthTalkData } from "../services/health-talk-api";


export const HealthTalk = () => {
  const columns: IColumnSpec<HealthTalkData>[] = [
    {
      name: "id",
      cell: (row) => row.id,
    },
    {
      name: "value",
      cell: (row) => row.value,
      width: "230px",
    },

  ];

  return (
    <div className="p-3">
      <h2>Health Talk</h2>
      <p>Health Talk Placeholder</p>
      <CustomTable
        datasource={segmentsSelector}
        columns={columns}
        pagingStore={pagingState}
      />
    </div>
  );
};
