function initMap() {
    // const center = { lat: 37.783, lng: -122.403 };
    const center = { lat: 37.231393, lng: -80.422373 };

    const mapOptions = {
        center: center,
        zoom: 20,
        heading: 50,
        tilt: 0,
        mapId: "90f87356969d889c",
        // zoomControl: false,
        // gestureHandling: "none",
    };
    const map = new google.maps.Map(document.getElementById("map"), mapOptions);

    const bounds = {
      17: [
        [20969, 20970],
        [50657, 50658],
      ],
      18: [
        [41939, 41940],
        [101315, 101317],
      ],
      19: [
        [83878, 83881],
        [202631, 202634],
      ],
      20: [
        [580079, 580083],
        [814581, 814586],
      ],
    };
    const imageMapType = new google.maps.ImageMapType({
      getTileUrl: function (coord, zoom) {
          console.log(coord.x, coord.y, zoom)
          bounds[zoom] = [
              [580080, 580080],
              [814583, 814583],
          ]
          if (
              zoom < 17 || zoom > 20 ||
              bounds[zoom][0][0] > coord.x ||
              coord.x > bounds[zoom][0][1] ||
              bounds[zoom][1][0] > coord.y ||
              coord.y > bounds[zoom][1][1]
          ) {
              return "";
          }

          return "FloorPlan.png"

          return "";

          return [
              "https://www.gstatic.com/io2010maps/tiles/5/L2_",
              zoom,
              "_",
              coord.x,
              "_",
              coord.y,
              ".png",
          ].join("");
      },
      tileSize: new google.maps.Size(128, 128),
    });

    map.overlayMapTypes.push(imageMapType);
  }

  window.initMap = initMap;
