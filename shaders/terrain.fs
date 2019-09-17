#version 330
in vec2 texCoords;
out vec4 FragColor;
uniform sampler2D terrainTexture;
uniform sampler2D rewardMap;
uniform sampler2D groundTruth;

uniform sampler2D tx1;
uniform sampler2D tx2;
uniform sampler2D tx3;
uniform sampler2D tx4;
uniform sampler2D tx5;

uniform int mode;

void main()
{    
    vec4 terrainColor = texture(terrainTexture, texCoords);
    vec4 rewardColor = texture(groundTruth, texCoords);
    vec4 tx1C = texture(tx1, texCoords*100);
    if(rewardColor.r == (80.0/255.0) && rewardColor.g == (78.0/255.0) && rewardColor.b == (63.0/255.0))
    {
        FragColor = tx1C;
    }
    else
    {
        FragColor = vec4(terrainColor.rgb, 1.0);
    }
    // if(mode == 0){
    //     if(rewardColor.r == (80.0/255.0) && rewardColor.g == (78.0/255.0) && rewardColor.b == (63.0/255.0))
    //     {
    //         FragColor = vec4(terrainColor.rgb, 1.0)*(0.7) + vec4(0.0, 0.0, 1.0, 0.3);
    //     }
    //     else
    //     {
    //         FragColor = vec4(terrainColor.rgb, 1.0);
    //     }
    // }
    // else{
    // }
}
