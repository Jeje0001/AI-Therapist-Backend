import React from "react";
import '../styles/Navbar.css';


function Navbar(){
    return(
    <>

<nav className="navbar navbar-expand-lg bg-dark fixed-top" role="navigation" aria-label="main navigation">
<div className="container-fluid d-flex justify-content-between align-items-center">



  <a className="navbar-brand brand" href="#">MindHaven</a>
  <div className="d-lg-none ms-auto">

  <button
  className="navbar-toggler navbar-toggler-icon-white d-lg-none"
  type="button"
  data-bs-toggle="offcanvas"
  data-bs-target="#mobileNav"
  aria-controls="mobileNav"
>
  <span className="navbar-toggler-icon"></span>
</button>
</div>

  <div className="d-none d-lg-flex gap-4 justify-content-center">


  <ul className="nav nav-pills ">
    <li className="nav-item">
      <a className="nav-link" href="#scrollspyHeading1" data-bs-dismiss="offcanvas">Features</a>
    </li>
    <li className="nav-item">
      <a className="nav-link" href="#scrollspyHeading2">How It Works</a>
    </li>
    <li className="nav-item">
      <a className="nav-link" href="#scrollspyHeading2">Faq</a>
    </li>
   
    
  </ul>

  </div>

    <div className=" d-none d-lg-flex gap-2">
  <button className="btn login">Login</button>
  <button className="btn signup">Sign up</button>
</div>
    </div>

  

    </nav>
    <div
  className="offcanvas offcanvas-end bg-dark text-white"
  tabIndex="-1"
  id="mobileNav"
  aria-labelledby="mobileNavLabel"
>
  <div className="offcanvas-header">
    <h5 className="offcanvas-title" id="mobileNavLabel">MindHaven</h5>
    <button
      type="button"
      className="btn-close btn-close-white"
      data-bs-dismiss="offcanvas"
      aria-label="Close"
    ></button>
  </div>
  <div className="offcanvas-body d-flex flex-column gap-3">
    <a href="#scrollspyHeading1" className="nav-link">Features</a>
    <a href="#scrollspyHeading2" className="nav-link">About</a>
    <a href="#scrollspyHeading2" className="nav-link">Faq</a>
    <hr className="bg-white" />
    <button className="btn login">Login</button>
    <button className="btn signup">Sign up</button>
  </div>
</div>
    </>


)
}

export default Navbar