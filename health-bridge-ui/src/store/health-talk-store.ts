import { atom, selector } from "recoil";
import { getHealthTalkData } from "../services/health-talk-api";
import { PageParam, PageSize } from "../services/common/service-types";


export const pagingState = atom<PageParam>({
  key: "pagingState",
  default: {
    offset: 0,
    limit: PageSize,
    page: 1,
  },
});

export const segmentsSelector = selector({
  key: "segmentsSelector",
  get: async ({ get }) => {
    const pageParam = get(pagingState);
    return await getHealthTalkData(pageParam);
  },
});
