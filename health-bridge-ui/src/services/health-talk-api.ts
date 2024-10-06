import { FetchResponse, getRequest, postRequest } from "./common/fetch-api";

export interface HealthTalkData {
    id: string;
    value: string;
}

export async function getHealthTalkData(

): Promise<FetchResponse<HealthTalkData[]>> {

    const response = await getRequest<HealthTalkData[]>({
        url: "/",
        params: {},
    });

    console.log(response)

    return response;
}
