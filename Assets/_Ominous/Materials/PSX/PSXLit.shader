Shader "Ominous/PSX Lit"
{
    Properties
    {
        _BaseMap ("Textura", 2D) = "white" {}
        _BaseColor ("Color", Color) = (1,1,1,1)
        _EmissionColor ("Emisión", Color) = (0,0,0,1)
        _AmbientBoost ("Ambiente extra (exterior)", Float) = 1
        _Exterior ("Niebla de exterior", Float) = 0
        _RoomAO ("Oscurecer junto a suelo y techo", Float) = 0
        _Stable ("Superficie grande sin temblor", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        float4 _PSX_SnapRes;   // x: ancho interno / 2, y: alto interno / 2, z: fuerza del snap
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half4 _EmissionColor;
            float _AmbientBoost;
            float _Exterior;
            float _RoomAO;
            float _Stable;
        CBUFFER_END
        float4 SnapVertex(float4 clip)
        {
            if (_Stable > 0.5 || _PSX_SnapRes.z <= 0.0 || clip.w <= 0.0) return clip;
            float2 ndc = clip.xy / clip.w;
            float2 snapped = round(ndc * _PSX_SnapRes.xy) / _PSX_SnapRes.xy;
            clip.xy = lerp(ndc, snapped, _PSX_SnapRes.z) * clip.w;
            return clip;
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _ADDITIONAL_LIGHTS _ADDITIONAL_LIGHTS_VERTEX
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            half4 _PSX_Ambient;
            half4 _PSX_FogColor;
            half4 _PSX_ExteriorFogColor;
            float4 _PSX_Params;   // x: afín, y-z: niebla interior, inicio y fin
            float4 _PSX_ExteriorFog; // x: inicio, y: fin

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float2 uv : TEXCOORD0; };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                noperspective float2 uvAffine : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
                float3 normalWS : TEXCOORD3;
            };

            Varyings Vert(Attributes i)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(i.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(i.normalOS);
                o.positionCS = SnapVertex(TransformWorldToHClip(o.positionWS));
                o.uv = TRANSFORM_TEX(i.uv, _BaseMap);
                o.uvAffine = o.uv;
                return o;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float2 uv = lerp(i.uv, i.uvAffine, _Stable > 0.5 ? 0.0 : _PSX_Params.x);
                half3 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, uv).rgb;
                half3 albedo = tex * _BaseColor.rgb;
                float3 n = normalize(i.normalWS);
                half3 light = _PSX_Ambient.rgb * _AmbientBoost;

                Light mainLight = GetMainLight();
                light += mainLight.color * mainLight.distanceAttenuation * saturate(dot(n, mainLight.direction));

                #if defined(_ADDITIONAL_LIGHTS)
                InputData inputData = (InputData)0;
                inputData.positionWS = i.positionWS;
                inputData.normalWS = n;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                uint pixelLightCount = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(pixelLightCount)
                    Light l = GetAdditionalLight(lightIndex, i.positionWS, half4(1,1,1,1));
                    light += l.color * l.distanceAttenuation * saturate(dot(n, l.direction));
                LIGHT_LOOP_END
                #endif

                if (_RoomAO > 0.5)
                {
                    float edge = saturate(min(i.positionWS.y / 0.4, (2.6 - i.positionWS.y) / 0.4));
                    light *= lerp(0.45, 1.0, edge);
                }

                half3 color = albedo * light + _EmissionColor.rgb * tex;
                // La niebla va por píxel: los suelos de la calle son polígonos muy grandes.
                float d = distance(i.positionWS, GetCameraPositionWS());
                if (_Exterior > 0.5)
                {
                    float fog = saturate((d - _PSX_ExteriorFog.x) / max(0.001, _PSX_ExteriorFog.y - _PSX_ExteriorFog.x));
                    color = lerp(color, _PSX_ExteriorFogColor.rgb, fog);
                }
                else
                {
                    float fog = saturate((d - _PSX_Params.y) / max(0.001, _PSX_Params.z - _PSX_Params.y));
                    color = lerp(color, _PSX_FogColor.rgb, fog);
                }
                return half4(color, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On
            ColorMask R
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            float4 Vert(float4 p : POSITION) : SV_POSITION { return SnapVertex(TransformObjectToHClip(p.xyz)); }
            half Frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }
}
