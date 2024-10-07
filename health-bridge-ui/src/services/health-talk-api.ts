import { FetchResponse, getRequest, postRequest } from "./common/fetch-api";
import { PageParam } from "./common/service-types";

export interface HealthTalkData {
    id: string;
    value: string;
}

export async function getHealthTalkData(
    pageParam: PageParam
): Promise<FetchResponse<HealthTalkData[]>> {

    // const response = await getRequest<HealthTalkData[]>({
    //     url: "/",
    //     params: {},
    // });

    const response = [
        '{"id":"Hello","value":"World"}',
        '{"id":"Hello2","value":"World2"}',
    ].map((r) => JSON.parse(r));
    return {
      success: true,
      data: response,
      total: response.length,
    };
}
