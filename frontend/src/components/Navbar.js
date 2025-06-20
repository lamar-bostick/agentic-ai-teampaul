import React from "react";

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg" style={{ backgroundColor: "#AB84FF" }}>
      <div className="container-fluid">
        <a className="navbar-brand text-white fw-bold" href="#">
          SkyBridge
        </a>
        <div className="collapse navbar-collapse">
          <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <a className="nav-link text-white" href="#">
                Home
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link text-white" href="#">
                Get Started
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
