import React from 'react';
import logo1  from '../../assets/images/customers logo/1.webp';
import logo2  from '../../assets/images/customers logo/2.webp';
import logo3  from '../../assets/images/customers logo/3.webp';
import logo4  from '../../assets/images/customers logo/4.webp';
import logo5  from '../../assets/images/customers logo/5.webp';
import logo6  from '../../assets/images/customers logo/6.webp';
import logo7  from '../../assets/images/customers logo/7.webp';
import logo8  from '../../assets/images/customers logo/8.webp';
import logo9  from '../../assets/images/customers logo/9.webp';
import logo10 from '../../assets/images/customers logo/10.webp';
import logo11 from '../../assets/images/customers logo/11.webp';
import logo12 from '../../assets/images/customers logo/12.webp';


const baseLogos = [
  logo1, logo2, logo3, logo4, logo5, logo6, 
  logo7, logo8, logo9, logo10, logo11, logo12
];

const allLogos = Array(30).fill(baseLogos).flat();

const LogoMarquee = () => {


  return (
    <div className="marquee-wrapper">
  <h2 className="text-lg sm:text-2xl mx-auto mb-8 mt-8 font-extrabold text-slate-600 text-center ">
  کڕیار و کۆمپانیاکان کە متمانەیان پێ کردووین
</h2>
      <div className="marquee-container" dir="ltr">
        <div className="marquee-track forward">
          {allLogos.map((logo, index) => (
            <img
              key={`forward-${index}`}
              src={logo}
              alt={`Customer Logo ${index + 1}`}
              className="marquee-logo"
            />
          ))}
        </div>
      </div>

      <div className="marquee-container" dir="ltr">
        <div className="marquee-track reverse">
          {allLogos.map((logo, index) => (
            <img
              key={`reverse-${index}`}
              src={logo}
              alt={`Customer Logo ${index + 1}`}
              className="marquee-logo"
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default LogoMarquee;