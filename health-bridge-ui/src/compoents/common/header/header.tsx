import {Navbar, NavbarBrand} from "reactstrap";
import { useRecoilValue } from "recoil";
import { userNameState } from "../../../store/user-store";

const Header = () => {
    const name = useRecoilValue(userNameState)

    return (
        <Navbar className="nav-bar" color='#000' light expand="md">
            <div className="ml-auto text-white">
                {name}
                <span>
                    Logout
                </span>
            </div>
        </Navbar>
    )
}

export default Header;