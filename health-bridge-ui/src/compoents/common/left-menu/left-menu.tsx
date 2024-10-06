import {Link, useLocation} from "react-router-dom";
import { Nav, NavItem } from "reactstrap";

const LeftMenu = () => {
    const { pathname} = useLocation();
    return (
        <Nav vertical className="side-menu" fill>
            <NavItem active={pathname === "/"}>
                <Link className="nav-link" to="/homepage">
                    <i className="fa fa-home" /> Homepage
                </Link>
            </NavItem>
        </Nav>
    );

};

export default LeftMenu;