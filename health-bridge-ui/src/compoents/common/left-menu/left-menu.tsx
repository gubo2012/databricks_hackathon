import {Link, useLocation} from "react-router-dom";
import { Nav, NavItem } from "reactstrap";

const LeftMenu = () => {
    const { pathname} = useLocation();
    return (
        <Nav vertical className="side-menu" fill>
            <NavItem active={pathname === "/" || pathname === "/homepage"}>
                <Link className="nav-link" to="/homepage">
                    <i className="fa fa-home" /> Homepage
                </Link>
            </NavItem>
            <NavItem active={pathname === "/healthtalk"}>
                <Link className="nav-link" to="/healthtalk">
                    <i className="fa fa-home" /> Health Talk
                </Link>
            </NavItem>
            <NavItem active={pathname === "/termexplore"}>
                <Link className="nav-link" to="/termexplore">
                    <i className="fa fa-home" /> Terms Explorer
                </Link>
            </NavItem>
        </Nav>
    );

};

export default LeftMenu;