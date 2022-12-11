
<a name="readme-top"></a>

[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://panel.sim-app.ovh">
    <img src="Assets/static/favicon.ico" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">SIM App for Device</h3>

  <p align="center">
    Send SMS from YOUR OWN and soon many more via API using our portal
    <br />
    <a href="https://panel.sim-app.ovh"><strong>See Sim App Panel</strong></a>
    
  </p>
</div>

<br><br>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#install-via-docker">Install Via Docker</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#possibilities">Possibilities</a></li>
    <li><a href="#updates">Updates</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

The application was written and tested on Python 3.7. Its purpose is to `communicate with the SIM800 overlay` connected to your device on which you run it, and it also `connects to our SIM App Controller` via WebSocket, so you do not need to have a public IP address etc. After connecting this software to the controller and selecting the USB port to which the overlay is connected, you do not have to do anything else there. Everything else is done by the controller. In the following points, I will show you what you can use the controller for, but first we will deal with the installation.

```
The application is distinguished by the fact that through our portal, using the api, you can send text messages from your own sim card :)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With


* ![RaspberryPI][RaspberryPI]
* ![Python37][Python37]
* ![Docker][Docker]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

For starters, you need an environment, preferably with linux.
<br>You also need to `buy a SIM800 overlay`


<br/>
<br/>

<div align="center"><a href="https://www.waveshare.com/gsm-gprs-gnss-hat.htm"><strong>$$$ Buy this sim overlay $$$</strong></a></div>

<br/>
<br/>
I am testing the application on the add-on from this link above. I highly recommend her. It is also equipped with audio support, which is worth having, because I will be expanding the application in this direction (tone dialing).

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* If you are using docker `(recommended)`
  ```sh
  curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
  ```
* If you want to install and use without docker
  ```sh
  apt install python3.7
  ```





### Install via docker `(recommended)`
<a name="install-via-docker"></a>
_Installation is very simple, because the software shown here is published in the [Docker Hub](https://hub.docker.com/r/karlos98/sim-app-device)_


* Download and run the image 
   ```sh
   docker run --privileged  -v ~/SIM-Data:/SIM-Data -p 8098:8098 -it karlos98/sim-app-device:amd

   ```

* If you are running on a raspberry pi change the tag to "pi"
  ```sh
  docker run --privileged  -v ~/SIM-Data:/SIM-Data -p 8098:8098 -it karlos98/sim-app-device:pi
  ```

* If you are installing on an unsupported platform build the container yourself using a Dockerfile with this content:
    ```text 
    FROM python:3.7.2
    RUN python3 -m pip install --upgrade pip
    RUN python3 -m pip install lci-sim-app-device
    CMD [ "python3", "-m", "lci-sim-app-device", "--dir=/SIM-Data" ]
    ```





<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Install via Python pip

_The package is published on [PyPi repository](https://pypi.org/project/lci-sim-app-device/), so you just need to install it on python 3.7_


* Make sure python is installed.
   ```sh
   apt install python3.7
   ```


* Install the python package via pip
   ```sh
   python3.7 -m pip install lci-sim-app-device
   ```

* Now you can run the application.
  ```sh
  python3 -m lci-sim-app-device --dir="~/SIM-Data"
  ```




<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!------ -- - - - --- - -- - -- - ------>


<!-- USAGE EXAMPLES -->
## Usage

After launching the application, you will find it on the default port 8098. So go to ```http://localhost:8098```



_Now you should configure the application._

1. Select Serial Port - select from the list the USB port to which the SIM shield is connected (which you should already have, or <a href="https://www.waveshare.com/gsm-gprs-gnss-hat.htm">buy</a>)
  ![product-screenshot-system-config]
If all goes well <b>Serial Status</b> should be green <b style="color:lime">Connected</b> like mine. In the future, if you change this port, restart the application.


2. Now connect the device to the <a href="https://panel.sim-app.ovh">Portal</a>, because after all everything will be done through it. To do this, you need to create an account <a href="https://panel.sim-app.ovh">here</a>. Then go to the list of devices in the portal and click the "Add Device" button. Enter the key generated there in the form below.
![product-screenshot-controller-config]
  After entering the key you should see <b>Socket Connection</b> status as <b style="color:yellow" >Connected, pending adopt</b>. You must then return to the controller where you will see your device listed and accept it.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Possibilities

_What does the application offer or will offer_

- [x] Connect with [Controller](https://panel.sim-app.ovh)
- [x] SMS
    - [x] Send
    - [x] Read
- [ ] USSD Code
    - [ ] Send
    - [ ] Receive
- [ ] Tone Dialing
- [ ] Receive incomming calls
- [ ] MMS
    - [ ] Send
    - [ ] Receive


<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Updates

_When you go to the webserver of the installed application (port 8098), you will see the versions of the application used at the top. When an update is available, a message will also be visible next to the version. Do them right away, because the changes may be so big that the device may not work properly. Now we will move on to how to perform such updates._

* If you are using docker (```choose "pi" or "amd" TAG!```)
  ```sh
  docker pull karlos98/sim-app-device:TAG_HERE
  ```


* If you are not using docker
  ```sh
  python3 -m pip install lci-sim-app-device -U
  ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

[Let's Code It](https://www.letscode.it), [Karol Sójka](https://facebook.com/Fadeusz) from Poland - kontakt@letscode.it

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Krzyś](https://github.com/krzys/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[product-screenshot]: Assets/static/screen-index.png
[product-screenshot-controller-config]: Assets/static/screen-controller-config.png
[product-screenshot-system-config]: Assets/static/screen-system-config.png


[license-shield]: https://img.shields.io/github/license/Let-s-Code-It/SIM-App-Device.svg?style=for-the-badge
[license-url]: https://github.com/Let-s-Code-It/SIM-App-Device//blob/master/LICENSE


[RaspberryPI]: https://img.shields.io/badge/Raspberry%20PI-red?style=for-the-badge&logo=raspberrypi&logoColor=white

[Python37]: https://img.shields.io/badge/Python%203.7-green?style=for-the-badge&logo=python&logoColor=white

[Docker]: https://img.shields.io/badge/Docker-blue?style=for-the-badge&logo=docker&logoColor=white