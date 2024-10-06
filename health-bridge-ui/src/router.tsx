import { Routes, Route, Outlet } from "react-router-dom";
import { HomePage } from "./compoents/home-page";

export const AppRouter = () => {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
            </Route>
        </Routes>
    );
};

const Layout = () => {
    return <Outlet />
}