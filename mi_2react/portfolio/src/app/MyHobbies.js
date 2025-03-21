function MyHobbies() {
    return (
      <div>
        {/* Hobby */}
        <h2>Hobby</h2>
        <video width="500" autoPlay loop controls>
          <source src="/assets/anime.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <hr />
  
        {/* YouTube Video */}
        <iframe
          width="560"
          height="315"
          src="https://www.youtube.com/embed/Ki_0iES2cGI?si=wUXVAHmhwx0AIvMe"
          title="YouTube video player"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerPolicy="strict-origin-when-cross-origin"
          allowFullScreen
        ></iframe>
      </div>
    );
  }

export default MyHobbies;