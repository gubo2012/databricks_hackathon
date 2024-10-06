import {atom, selector} from "recoil";

export interface Auth {
    name: string;
}

export const authState = atom<Auth | null>({
    key: "authState",
    default: null,
});

export const userNameState = selector({
    key: "useNameState",
    get: ({ get}) => get(authState)?.name
})