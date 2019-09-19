#version 330
in vec2 texCoords;

uniform sampler2D terrainTexture;
uniform sampler2D groundTruth;

uniform sampler2D tx1;
uniform sampler2D tx2;
uniform sampler2D tx3;
uniform sampler2D tx4;
uniform sampler2D tx5;

uniform sampler2D predictedRewards;
uniform sampler2D predictedNovelty;
uniform sampler2D path;

uniform int mode;
uniform int maskMode;

out vec4 FragColor;

vec4 getTextureColor(vec4 gt)
{
    int tiling = 50;
    vec4 texColor = vec4(0.0);

    if (abs(gt.r*255.0 - 125.0) < 1.0){
        texColor = texture(tx2, texCoords*tiling);
    }
    else if (abs(gt.r*255.0 - 79.0) < 1.0){
        texColor = texture(tx3, texCoords*tiling);
    }
    else if (abs(gt.r*255.0 - 122.0) < 1.0){
        texColor = texture(tx4, texCoords*tiling);
    }
    else if (abs(gt.r*255.0 - 181.0) < 1.0){
        texColor = texture(tx5, texCoords*tiling);
    }
    else if (abs(gt.r*255.0 - 120.0) < 1.0){
        texColor = texture(tx1, texCoords*tiling);
    }
    else{
        texColor = vec4(1.0);
    }
    
    return texColor;
}

void main()
{    
    vec4 terrainColor = texture(terrainTexture, texCoords);
    vec4 gtColor = texture(groundTruth, texCoords);
    vec4 rewardColor = texture(predictedRewards, texCoords);
    vec4 novelty = texture(predictedNovelty, texCoords);
    vec4 path = texture(path, texCoords);
    vec4 renderColor = vec4(1.0);
    switch(mode){
        case 0:
            renderColor = terrainColor;
            break;
        case 1:
            renderColor = gtColor;
            break;
        case 2:
            renderColor = rewardColor;
            break;
        case 3:
            renderColor = novelty;
            break;
        case 4:
            renderColor = path;
            break;
    }

    // vec4 textureColor = getTextureColor();
    // vec4 maskColor = calculateMaskColor();
    renderColor = getTextureColor(gtColor);
    FragColor = renderColor;   
}



// Color code segmentation result

// Assign textures to colors

// Create dataset

// Learning code

// API for 4 frame buffers

// 2D Map from FPV prediction

// Mask

// GUI stuff