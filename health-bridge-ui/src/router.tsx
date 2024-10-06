import { Routes, Route, Outlet } from "react-router-dom";
import { HomePage } from "./compoents/home-page";
import { HealthTalk } from "./compoents/health-talk";
import { TermsExplorer } from "./compoents/term-explore";

export const AppRouter = () => {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
            </Route>
            <Route path="/homepage" element={<Layout />}>
                <Route index element={<HomePage />} />
            </Route>
            <Route path="/healthtalk" element={<Layout />}>
                <Route index element={<HealthTalk />} />
            </Route>
            <Route path="/termexplore" element={<Layout />}>
                <Route index element={<TermsExplorer />} />
            </Route>
        </Routes>
    );
};

const Layout = () => {
    return <Outlet />
}