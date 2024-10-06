import axios, {AxiosResponse} from "axios";
import { toast } from "react-toastify";

export const Axios = axios.create({
    baseURL: "/",
});

export interface FetchResponse<T> {
    success: boolean;
    data?: T;
    total?: number;
    error?: string;
    axiosResponse?: AxiosResponse<T, any>;
}

interface FetchRequestParam {
    url: string;
    params?: Record<string, string>;
    data?: unknown;
}


function processError(e: any) {
    const status = e.response.status;
    if ([500].includes(status)) {
        toast.error("Server error!")
    }
    return {
        success: false,
        error: e.response?.data ?? e.message,
    }
}

export const getRequest = async <T>({
    url,
    params,
}: FetchRequestParam): Promise<FetchResponse<T>> => {
    try {
        const response = await Axios.get<T>(url, {params});

        return {
            success: true,
            data: response.data,
            axiosResponse: response,
        };
    } catch (e) {
        return processError(e);
    }
}

export const postRequest = async <T>({
    url,
    params,
    data,
}: FetchRequestParam): Promise<FetchResponse<T>> => {
    try {
        const response = await Axios.post<T>(url, data, {params});

        return {
            success: true,
            data: response.data,
            axiosResponse: response,
        };
    } catch (e) {
        return processError(e);
    }
}