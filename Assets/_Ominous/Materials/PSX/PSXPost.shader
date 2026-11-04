Shader "Hidden/Ominous/PSX Post"
{
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Name "PSXPost"
            ZTest Always ZWrite Off Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            float4 _PSX_Post;  // x: tramado, y: niveles por canal, z: brillo
            float4 _PSX_Grade; // x: contraste, y: saturación, z: tinte de sombras

            static const float BAYER[16] = {
                 0.0,  8.0,  2.0, 10.0,
                12.0,  4.0, 14.0,  6.0,
                 3.0, 11.0,  1.0,  9.0,
                15.0,  7.0, 13.0,  5.0 };

            half4 Frag(Varyings i) : SV_Target
            {
                half3 c = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_PointClamp, i.texcoord).rgb;
                #if !defined(UNITY_COLORSPACE_GAMMA)
                c = LinearToSRGB(c);
                #endif
                c = saturate(c * _PSX_Post.z);
                // Etalonaje con pivote bajo para no perder los tonos medios: negros profundos, color apagado y sombras hacia el granate.
                c = saturate((c - 0.28) * _PSX_Grade.x + 0.28);
                float luma = dot(c, float3(0.299, 0.587, 0.114));
                c = lerp(luma.xxx, c, _PSX_Grade.y);
                float shadow = 1.0 - smoothstep(0.0, 0.55, luma);
                c *= lerp(float3(1.0, 1.0, 1.0), float3(1.08, 0.84, 0.8), shadow * _PSX_Grade.z);
                float levels = max(2.0, _PSX_Post.y);
                uint2 p = (uint2)i.positionCS.xy % 4;
                float threshold = (BAYER[p.x + p.y * 4] + 0.5) / 16.0 - 0.5;
                c += threshold * _PSX_Post.x / levels;
                c = floor(saturate(c) * (levels - 1.0) + 0.5) / (levels - 1.0);
                #if !defined(UNITY_COLORSPACE_GAMMA)
                c = SRGBToLinear(c);
                #endif
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
