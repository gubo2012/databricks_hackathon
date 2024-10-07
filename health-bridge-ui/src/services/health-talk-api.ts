import { FetchResponse, getRequest, postRequest } from "./common/fetch-api";
import { PageParam } from "./common/service-types";

export interface HealthTalkData {
    id: string;
    value: string;
}

export async function getHealthTalkData(
    pageParam: PageParam
): Promise<FetchResponse<HealthTalkData[]>> {

    const response = await getRequest<HealthTalkData[]>({
        url: "http://44.203.65.128",
        params: {},
    });

    console.log("Response Data:", response.data);

    const transformedData: HealthTalkData[] = Object.entries(response.data).map(([key, value]) => ({
        id: key,
        value: value,
    }));

    console.log("Transformed Data:", transformedData);

    return {
      success: true,
      data: transformedData,
      total: transformedData.length,
    };


    // try with mock data

    // const response = [
    //     '{"id":"Hello","value":"World"}',
    //     '{"id":"Hello2","value":"World2"}',
    // ].map((r) => JSON.parse(r));
    // return {
    //   success: true,
    //   data: response,
    //   total: response.length,
    // };
}
